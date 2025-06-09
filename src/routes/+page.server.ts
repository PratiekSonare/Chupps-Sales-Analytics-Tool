// src/routes/+page.server.ts
import type { PageServerLoad } from './$types';
import { supabase } from '../lib/supabaseClient';

export const load: PageServerLoad = async () => {
  // Query the table
  const { data: wo_centro_prophet, error: err1 } = await supabase.from('wo_centro_prophet').select('*');
  const { data: chupps_items_noSort, error: err3 } = await supabase.from('unique_items_view').select('item');
  const { data: chupps_sales, error: err2 } = await supabase.from('total_sales').select('sales');
  const { data: chupps_revenue, error: err4 } = await supabase.from('total_revenue').select('revenue');
  const { data: chupps_parties, error: err5 } = await supabase.from('total_parties').select('');

  if (err1 || err2 || err3) {
    console.error('Supabase error:', err1 || err2 || err3);
    return { wo_centro_prophet: [], total_sales: 0 }; // Return an empty array on error
  } else {
    console.log('Data fetched successfully!');
  }

  const total_sales = chupps_sales[0].sales;
  const total_revenue = chupps_revenue[0].revenue;

  const total_parties = chupps_parties[0].party;
  const chupps_items = chupps_items_noSort?.sort();

  console.log('chupps_items: ', chupps_sales)
  return {
    wo_centro_prophet, total_sales, total_revenue, total_parties, chupps_items
  };
};
