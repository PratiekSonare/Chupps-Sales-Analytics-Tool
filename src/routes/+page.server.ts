// src/routes/+page.server.ts
import type { PageServerLoad } from './$types';
import { supabase } from '../lib/supabaseClient';

export const load: PageServerLoad = async () => {
  // Query the table
  const { data: wo_centro_prophet, error: err1 } = await supabase.from('wo_centro_prophet').select('*');
  // const { data: non_zero_no_spikes_prophet, error: err8 } = await supabase.from('nonzero_prophet').select('*');
  const { data: chupps_23_25_full, error: err6 } = await supabase.from('chupps_23_25_full').select('*');
  // const { data: chupps_23_25_full_nospikes, error: err9 } = await supabase.from('chupps_23_25_full_nospikes').select('*');
  const { data: chupps_items_noSort, error: err3 } = await supabase.from('unique_items_view').select('item');
  const { data: chupps_shades_noSort, error: err7 } = await supabase.from('total_shades').select('shade');
  const { data: chupps_sales, error: err2 } = await supabase.from('total_sales').select('sales');
  const { data: chupps_revenue, error: err4 } = await supabase.from('total_revenue').select('revenue');
  const { data: chupps_parties, error: err5 } = await supabase.from('total_parties').select('');
  const { data: itemFilteredDB, error: err10 } = await supabase.from('chupps_23_25_full').select('item', {count: 'exact'}).order('item', {ascending: true});
  const { data: ranked_items_by_sales, error: err11} = await supabase.from('ranked_items_by_sales').select('*');
  const { data: ranked_shades_by_sales, error: err12} = await supabase.from('ranked_shades_by_sales').select('*');
  
  if (err1 || err2 || err3 || err11 ) {
    console.error('Supabase error:', err1 || err2 || err3);
  } else {
    console.log('Data fetched successfully!');
  }
  
  const total_sales = chupps_sales[0].sales;
  const total_revenue = chupps_revenue[0].revenue;
  const total_parties = chupps_parties[0].party;
  const chupps_items = chupps_items_noSort;
  const chupps_shades = chupps_shades_noSort;

  return {
    wo_centro_prophet, chupps_23_25_full, ranked_items_by_sales, ranked_shades_by_sales, total_sales, total_revenue, total_parties, chupps_items, chupps_shades, itemFilteredDB
  };
};
